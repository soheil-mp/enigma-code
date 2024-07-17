import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, PeftModel, prepare_model_for_kbit_training
from trl import SFTTrainer
from huggingface_hub import HfApi

class Llama3FineTuner:
    def __init__(self, model_name, dataset_name, output_dir):
        self.model_name = model_name
        self.dataset_name = dataset_name
        self.output_dir = output_dir
        self.tokenizer = None
        self.model = None
        self.trainer = None

    def load_model_and_tokenizer(self):
        # Quantization configuration
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )

        # Load the model with quantization
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
        )
        self.model.config.use_cache = False
        self.model.config.pretraining_tp = 1

        # Load the tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"

        # Prepare the model for k-bit training
        self.model = prepare_model_for_kbit_training(self.model)

    def setup_training(self, num_train_epochs=3, per_device_train_batch_size=4):
        # LoRA configuration
        peft_config = LoraConfig(
            lora_alpha=16,
            lora_dropout=0.1,
            r=64,
            bias="none",
            task_type="CAUSAL_LM",
        )

        # Load and preprocess the dataset
        dataset = load_dataset(self.dataset_name)
        train_dataset = dataset["train"]

        # Training arguments
        training_arguments = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=num_train_epochs,
            per_device_train_batch_size=per_device_train_batch_size,
            gradient_accumulation_steps=4,
            optim="paged_adamw_32bit",
            save_steps=25,
            logging_steps=25,
            learning_rate=2e-4,
            weight_decay=0.001,
            fp16=True,
            bf16=False,
            max_grad_norm=0.3,
            max_steps=-1,
            warmup_ratio=0.03,
            group_by_length=True,
            lr_scheduler_type="constant",
        )

        # Initialize the SFTTrainer
        self.trainer = SFTTrainer(
            model=self.model,
            train_dataset=train_dataset,
            peft_config=peft_config,
            dataset_text_field="text",
            max_seq_length=512,
            tokenizer=self.tokenizer,
            args=training_arguments,
        )

    def train(self):
        self.trainer.train()

    def save_model(self):
        self.trainer.model.save_pretrained(self.output_dir)

    def merge_and_save(self):
        # Merge the LoRA weights with the base model
        base_model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map="auto",
        )
        ft_model = PeftModel.from_pretrained(base_model, self.output_dir)
        merged_model = ft_model.merge_and_unload()

        # Save the merged model
        merged_model.save_pretrained("./merged_llama3_ft")
        self.tokenizer.save_pretrained("./merged_llama3_ft")

    def push_to_hub(self, repo_id):
        api = HfApi()
        api.upload_folder(
            folder_path="./merged_llama3_ft",
            repo_id=repo_id,
            repo_type="model",
        )

    def inference(self, prompt, max_length=100):
        from transformers import pipeline

        pipe = pipeline("text-generation", model="./merged_llama3_ft", tokenizer="./merged_llama3_ft")
        generated_text = pipe(prompt, max_length=max_length, do_sample=True, top_k=50, top_p=0.95)
        return generated_text[0]['generated_text']

# Usage example
if __name__ == "__main__":
    fine_tuner = Llama3FineTuner(
        model_name="meta-llama/Llama-3-8b-hf",
        dataset_name="your_dataset_name",
        output_dir="./results_llama3_ft"
    )

    fine_tuner.load_model_and_tokenizer()
    fine_tuner.setup_training(num_train_epochs=3, per_device_train_batch_size=4)
    fine_tuner.train()
    fine_tuner.save_model()
    fine_tuner.merge_and_save()

    # Optional: Push to Hugging Face Hub
    # fine_tuner.push_to_hub("your-username/your-model-name")

    # Inference example
    prompt = "What is the capital of France?"
    generated_text = fine_tuner.inference(prompt)
    print(generated_text)



import openai
import os
import json
from time import sleep

class OpenAIFineTuner:
    def __init__(self, api_key, model="gpt-3.5-turbo"):
        self.api_key = api_key
        openai.api_key = self.api_key
        self.base_model = model
        self.file_id = None
        self.job_id = None
        self.fine_tuned_model = None

    def prepare_training_data(self, input_file, output_file):
        """
        Prepare the training data in the format required by OpenAI.
        Input file should be a CSV with 'prompt' and 'completion' columns.
        """
        import pandas as pd

        df = pd.read_csv(input_file)
        training_data = []

        for _, row in df.iterrows():
            training_data.append({
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": row['prompt']},
                    {"role": "assistant", "content": row['completion']}
                ]
            })

        with open(output_file, 'w') as f:
            for item in training_data:
                f.write(json.dumps(item) + '\n')

        print(f"Training data prepared and saved to {output_file}")

    def upload_training_file(self, file_path):
        """Upload the training file to OpenAI."""
        with open(file_path, "rb") as file:
            response = openai.File.create(file=file, purpose="fine-tune")
        self.file_id = response.id
        print(f"File uploaded with ID: {self.file_id}")

    def start_fine_tuning(self):
        """Start the fine-tuning job."""
        response = openai.FineTuningJob.create(
            training_file=self.file_id,
            model=self.base_model
        )
        self.job_id = response.id
        print(f"Fine-tuning job started with ID: {self.job_id}")

    def check_fine_tuning_status(self):
        """Check the status of the fine-tuning job."""
        while True:
            response = openai.FineTuningJob.retrieve(self.job_id)
            status = response.status
            print(f"Fine-tuning status: {status}")
            if status == "succeeded":
                self.fine_tuned_model = response.fine_tuned_model
                print(f"Fine-tuning completed. Model ID: {self.fine_tuned_model}")
                break
            elif status == "failed":
                print("Fine-tuning failed.")
                break
            sleep(60)  # Check every minute

    def test_fine_tuned_model(self, prompt):
        """Test the fine-tuned model with a prompt."""
        if not self.fine_tuned_model:
            print("No fine-tuned model available.")
            return

        response = openai.ChatCompletion.create(
            model=self.fine_tuned_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    def run_fine_tuning_process(self, input_file, prepared_file):
        """Run the entire fine-tuning process."""
        self.prepare_training_data(input_file, prepared_file)
        self.upload_training_file(prepared_file)
        self.start_fine_tuning()
        self.check_fine_tuning_status()

# Usage example
if __name__ == "__main__":
    api_key = "your-openai-api-key"
    fine_tuner = OpenAIFineTuner(api_key)

    # Run the fine-tuning process
    fine_tuner.run_fine_tuning_process(
        input_file="your_input_data.csv",
        prepared_file="prepared_training_data.jsonl"
    )

    # Test the fine-tuned model
    if fine_tuner.fine_tuned_model:
        test_prompt = "What is the capital of France?"
        response = fine_tuner.test_fine_tuned_model(test_prompt)
        print(f"Test prompt: {test_prompt}")
        print(f"Model response: {response}")